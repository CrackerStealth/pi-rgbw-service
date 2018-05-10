var config = {
   entry: './app/Main.jsx',
   output: {
      filename: 'index.js',
   },
   devServer: {
      inline: true,
      port: 8080,
      disableHostCheck: true,
      https: false,
   },
   module: {
      rules: [
         {
             test: /\.jsx$/,
             exclude: /node_modules/,
             use: {
                loader: "babel-loader"
             }
         }
      ]
   }
}

module.exports = config;