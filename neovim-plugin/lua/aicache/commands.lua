-- Command registration and handling
local M = {}

function M.register()
  -- Register user commands
  vim.api.nvim_create_user_command('AicacheQuery', function(opts)
    local prompt = opts.args
    if prompt == "" then
      prompt = vim.fn.input("Query: ")
    end
    
    if prompt ~= "" then
      local response = require('aicache').query(prompt)
      if response then
        -- Show response in floating window
        require('aicache.ui.float').show(response)
      end
    end
  end, { nargs = "?" })
  
  vim.api.nvim_create_user_command('AicacheRefresh', function()
    require('aicache').refresh()
    vim.notify("Cache refreshed", vim.log.levels.INFO)
  end, {})
  
  -- Set up keymaps
  local keymaps = {
    query = "<C-a>",
    refresh = "<C-r>",
  }
  vim.keymap.set('n', keymaps.query, '<Cmd>AicacheQuery<CR>', { desc = "Query aicache" })
  vim.keymap.set('n', keymaps.refresh, '<Cmd>AicacheRefresh<CR>', { desc = "Refresh aicache" })
end

return M