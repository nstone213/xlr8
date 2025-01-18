const path = require('path');

module.exports = {
    entry: './src/index.js', // Your main JavaScript file
    output: {
        filename: 'bundle.js', // Output file name
        path: path.resolve(__dirname, 'dist'), // Output directory
    },
    mode: 'development',
};
