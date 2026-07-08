import fs from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'

const require = createRequire(process.cwd() + '/')
const { chromium } = require('playwright')

const scenarioPath = process.argv[2]
if (!scenarioPath) {
  console.error('usage: node ui_sim_runner.mjs <scenario.json>')
  process.exit(2)
}

const resolvedScenarioPath = path.resolve(scenarioPath)
const scenarioDir = path.dirname(resolvedScenarioPath)
const scenario = JSON.parse(await fs.readFile(resolvedScenarioPath, 'utf8'))
const baseUrl = process.env.CAIRN_UI_BASE_URL || scenario.baseUrl || 'http://localhost:5273'
const outputSetting = process.env.CAIRN_UI_OUTPUT || scenario.output || '../analysis/ui-sim-report.json'
const output = path.isAbsolute(outputSetting) ? outputSetting : path.resolve(scenarioDir, outputSetting)
const headed = process.env.CAIRN_UI_HEADED === '1'
const defaultTimeout = Number(process.env.CAIRN_UI_TIMEOUT || scenario.timeout || 30000)
const screenshotsSetting = scenario.screenshotsDir || path.join(path.dirname(output), 'screenshots')
const screenshotsDir = path.isAbsolute(screenshotsSetting)
  ? screenshotsSetting
  : path.resolve(scenarioDir, screenshotsSetting)

const report = {
  scenario: scenario.name || path.basename(scenarioPath),
  baseUrl,
  startedAt: new Date().toISOString(),
  metrics: {
    clicks: 0,
    fills: 0,
    assertions: 0,
    waits: 0,
    screenshots: 0,
    contextSwitches: 0,
    popups: 0,
    layoutSnapshots: 0,
  },
  observations: [],
  findings: [],
  layoutLoad: [],
  screenshots: [],
  errors: [],
}

const browser = await chromium.launch({ headless: !headed, args: ['--no-sandbox'] })
const context = await browser.newContext({ viewport: scenario.viewport || { width: 1280, height: 800 } })
let page = await context.newPage()
page.setDefaultTimeout(defaultTimeout)

try {
  await page.goto(baseUrl, { waitUntil: scenario.waitUntil || 'domcontentloaded' })
  report.observations.push({ type: 'goto', url: page.url() })
  for (const step of scenario.steps || []) {
    await runStep(step)
  }
} catch (error) {
  report.errors.push(String(error?.stack || error))
} finally {
  report.finishedAt = new Date().toISOString()
  await fs.mkdir(path.dirname(output), { recursive: true })
  await fs.writeFile(output, JSON.stringify(report, null, 2))
  console.log(JSON.stringify(report, null, 2))
  await browser.close()
}

process.exit(report.errors.length ? 1 : 0)

async function runStep(step) {
  const label = step.label || step.action
  if (step.humanLoad) {
    report.observations.push({ type: 'human_load', label, ...step.humanLoad })
  }
  if (step.contextSwitch) report.metrics.contextSwitches += 1

  switch (step.action) {
    case 'click':
      await locatorFor(step).click()
      report.metrics.clicks += 1
      report.observations.push(selectorObservation('click', label, step))
      break
    case 'fill':
      await locatorFor(step).fill(step.value || '')
      report.metrics.fills += 1
      report.observations.push({ ...selectorObservation('fill', label, step), chars: (step.value || '').length })
      break
    case 'press':
      await locatorFor(step).press(step.key)
      report.observations.push({ ...selectorObservation('press', label, step), key: step.key })
      break
    case 'select':
      await locatorFor(step).selectOption(step.value)
      report.observations.push({ ...selectorObservation('select', label, step), value: step.value })
      break
    case 'waitForSelector':
      await page.waitForSelector(step.selector, { timeout: step.timeout || defaultTimeout })
      report.metrics.waits += 1
      report.observations.push({ type: 'waitForSelector', label, selector: step.selector })
      break
    case 'waitForText':
      await page.getByText(step.text, { exact: Boolean(step.exact) }).waitFor({ timeout: step.timeout || defaultTimeout })
      report.metrics.waits += 1
      report.observations.push({ type: 'waitForText', label, text: step.text })
      break
    case 'waitForCountAtLeast':
      await page.waitForFunction(
        ({ selector, count }) => document.querySelectorAll(selector).length >= count,
        { selector: step.selector, count: step.count },
        { timeout: step.timeout || defaultTimeout },
      )
      report.metrics.waits += 1
      report.observations.push({ type: 'waitForCountAtLeast', label, selector: step.selector, expected: step.count })
      break
    case 'assertVisible':
      await locatorFor(step).waitFor({ state: 'visible', timeout: step.timeout || defaultTimeout })
      report.metrics.assertions += 1
      report.observations.push(selectorObservation('assertVisible', label, step))
      break
    case 'assertCountAtLeast': {
      const count = await page.locator(step.selector).count()
      const ok = count >= step.count
      report.metrics.assertions += 1
      report.observations.push({ type: 'assertCountAtLeast', label, selector: step.selector, count, expected: step.count, ok })
      if (!ok) throw new Error(`${label}: expected at least ${step.count} matches for ${step.selector}, got ${count}`)
      break
    }
    case 'assertTextIncludes': {
      const text = await locatorFor(step).innerText()
      const ok = text.includes(step.text)
      report.metrics.assertions += 1
      report.observations.push({ ...selectorObservation('assertTextIncludes', label, step), text: step.text, ok })
      if (!ok) throw new Error(`${label}: expected ${step.selector} text to include ${step.text}`)
      break
    }
    case 'waitForNonEmptyText':
      await page.waitForFunction(
        (selector) => {
          const els = Array.from(document.querySelectorAll(selector))
          const el = els[els.length - 1]
          return el && !el.querySelector('.typing') && el.textContent.trim().length > 0
        },
        step.selector,
        { timeout: step.timeout || defaultTimeout },
      )
      report.metrics.waits += 1
      report.observations.push(selectorObservation('waitForNonEmptyText', label, step))
      break
    case 'screenshot': {
      await fs.mkdir(screenshotsDir, { recursive: true })
      const file = path.join(screenshotsDir, step.name || `${report.metrics.screenshots + 1}.png`)
      await page.screenshot({ path: file, fullPage: Boolean(step.fullPage) })
      report.metrics.screenshots += 1
      report.screenshots.push(file)
      report.observations.push({ type: 'screenshot', label, file })
      break
    }
    case 'popup': {
      const [popup] = await Promise.all([
        context.waitForEvent('page'),
        locatorFor(step).click(),
      ])
      await popup.waitForLoadState('domcontentloaded')
      report.metrics.clicks += 1
      report.metrics.popups += 1
      report.metrics.contextSwitches += 1
      report.observations.push({ type: 'popup', label, selector: step.selector, url: popup.url() })
      if (step.assertUrlIncludes && !popup.url().includes(step.assertUrlIncludes)) {
        throw new Error(`${label}: popup URL did not include ${step.assertUrlIncludes}`)
      }
      if (step.close !== false) await popup.close()
      break
    }
    case 'finding':
      report.findings.push({ label, ...step.value })
      break
    case 'measureLayout': {
      const snapshot = await measureLayout(step, label)
      report.metrics.layoutSnapshots += 1
      report.layoutLoad.push(snapshot)
      report.observations.push({ type: 'measureLayout', label, elements: snapshot.elements.length })
      break
    }
    default:
      throw new Error(`Unknown scenario action: ${step.action}`)
  }
}

function locatorFor(step) {
  const locator = page.locator(step.selector)
  return Number.isInteger(step.index) ? locator.nth(step.index) : locator.first()
}

function selectorObservation(type, label, step) {
  return Number.isInteger(step.index)
    ? { type, label, selector: step.selector, index: step.index }
    : { type, label, selector: step.selector }
}

async function measureLayout(step, label) {
  const viewport = page.viewportSize() || scenario.viewport || { width: 1280, height: 800 }
  const elements = []
  for (const spec of step.elements || []) {
    const locator = Number.isInteger(spec.index)
      ? page.locator(spec.selector).nth(spec.index)
      : page.locator(spec.selector).first()
    await locator.waitFor({ state: 'visible', timeout: spec.timeout || step.timeout || defaultTimeout })
    const box = await locator.boundingBox()
    if (!box) continue
    elements.push({
      id: spec.id,
      role: spec.role || 'element',
      label: spec.label,
      group: spec.group,
      selector: spec.selector,
      x: box.x,
      y: box.y,
      width: box.width,
      height: box.height,
    })
  }
  return {
    label,
    viewport,
    elements,
    relations: step.relations || [],
    sequence: step.sequence || [],
  }
}
