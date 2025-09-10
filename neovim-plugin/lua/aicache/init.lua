-- Main aicache plugin module
local M = {}

-- Default configuration
local config = {
  enabled = true,
  service_url = "http://localhost:8080",
  enable_collaboration = false,
  keymaps = {
    query = "<C-a>",
    refresh = "<C-r>",
  },
}

-- Setup function
function M.setup(opts)
  -- Merge user options with defaults
  config = vim.tbl_deep_extend("force", config, opts or {})
  
  -- Initialize components
  require('aicache.commands').register()
  require('aicache.ui.status').setup()
  
  vim.notify("aicache plugin initialized", vim.log.levels.INFO)
end

-- Public API
function M.query(prompt)
  return require('aicache.cache').query(prompt, require('aicache.context').get())
end

function M.refresh()
  require('aicache.cache').refresh()
end

return M