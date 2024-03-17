const React = require("react");

const LogView = (props) => {
    const { logs } = props.remote;
    return <div
        onClick={this.handleClick}
        style={{ display: "flex", flexDirection: "column", padding: 5, height: "100%", overflow: "hidden" }}
    >
        <h2>Logs</h2>
        <div style={{ flexGrow: 1, overflow: "scroll", fontFamily: "monospace" }}>
            {logs.map(log => <div>{log}</div>)}
        </div>
    </div>
}

module.exports = { LogView }