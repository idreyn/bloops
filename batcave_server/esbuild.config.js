const esbuild = require('esbuild');

esbuild.build({
    entryPoints: ['src/main.jsx'],
    bundle: true,
    outdir: 'dist',
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