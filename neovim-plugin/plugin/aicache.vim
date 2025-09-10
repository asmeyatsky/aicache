" Vimscript entry point
if exists('g:loaded_aicache')
  finish
endif
let g:loaded_aicache = 1

" Initialize the plugin with default settings
lua require('aicache').setup()