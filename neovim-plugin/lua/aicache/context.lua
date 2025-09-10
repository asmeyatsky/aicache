-- Context provider
local M = {}

local current_context = {}

function M.update()
  -- Get current buffer information
  local buf = vim.api.nvim_get_current_buf()
  local bufname = vim.api.nvim_buf_get_name(buf)
  local filetype = vim.api.nvim_buf_get_option(buf, 'filetype')
  
  -- Get cursor position
  local cursor = vim.api.nvim_win_get_cursor(0)
  
  current_context = {
    language = filetype,
    filename = bufname,
    line = cursor[1],
    column = cursor[2],
    cwd = vim.fn.getcwd()
  }
end

function M.get()
  return current_context
end

-- Update context when module is loaded
M.update()

return M