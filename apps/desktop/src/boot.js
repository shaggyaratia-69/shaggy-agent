const progress = document.getElementById('progress')
const message = document.getElementById('message')
const logs = document.getElementById('logs')

function render(state) {
  progress.style.width = `${Math.max(0, Math.min(100, state.progress || 0))}%`
  message.textContent = state.error ? `Error: ${state.error}` : (state.message || 'Starting Shaggy The Agent…')
  const lines = state.logs && state.logs.length ? state.logs : ['Waiting for startup logs…']
  logs.textContent = lines.join('\n')
  logs.scrollTop = logs.scrollHeight
}

if (window.shaggyDesktop?.onBoot) {
  window.shaggyDesktop.onBoot(render)
}
