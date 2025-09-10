-- Status line component
local M = {}

function M.setup()
  -- Set up statusline component
  vim.o.statusline = "%{%v:lua.require('aicache.ui.status').render()%}"
end

function M.render()
  -- Simple status indicator
  return " aicache "
end

return M