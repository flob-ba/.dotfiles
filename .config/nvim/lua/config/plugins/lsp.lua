return {
    {"VonHeikemen/lsp-zero.nvim", branch = "v3.x"},
    {
        "neovim/nvim-lspconfig",
        opts = {
            function()
                return {
                    diagnostics = {
                        update_in_insert = true,
                    }
                }
            end,
        },
        config = function(_,opts)
            vim.diagnostic.config(vim.deepcopy(opts.diagnostics))
        end,
    }
}
