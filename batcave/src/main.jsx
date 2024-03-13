const React = require("react");
const { render } = require("react-dom");

const injectTapEventPlugin = require("react-tap-event-plugin");
injectTapEventPlugin();

const MuiThemeProvider = require("material-ui/styles/MuiThemeProvider").default;

require("../css/style.css");

const { Backend } = require("./backend.js");
const { Remote } = require("./remote.js");
const { ConnectionManager } = require("./connection-manager.js");

const { RobinApp } = require("./views/app.jsx");

var appRoot;
document.addEventListener("DOMContentLoaded", function () {
    appRoot = document.getElementById("root");
    update();
});

function update() {
    if (appRoot) render(<MuiThemeProvider>
        <RobinApp remote={remote} connectionManager={connectionManager} />
    </MuiThemeProvider>, appRoot);
}

const backend = new Backend();
const connectionManager = new ConnectionManager(update, backend);
const remote = new Remote(update, backend);

window.backend = backend;
