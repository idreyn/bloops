const esbuild = require('esbuild');

const devMode = process.argv.includes("--dev");

const main = async () => {
    const ctx = await esbuild.context({
        entryPoints: ['src/main.jsx'],
        bundle: true,
        outdir: 'dist',
        minify: !devMode,
        loader: {
            // Set the loader options for image files
            '.jpg': 'file',
            '.jpeg': 'file',
            '.png': 'file',
            '.gif': 'file',
            '.svg': 'file',
        },
        // Define a public path or URL where assets will be served from
        publicPath: '/assets',
        // Configure asset names to retain directory structure relative to 'src' folder
        assetNames: 'assets/[dir]/[name]-[hash]',
        // ...other options
    }).catch(() => process.exit(1));
    await ctx.rebuild();
    if (devMode) {
        await ctx.watch();
    }
}

main().then(() => process.exit(0));