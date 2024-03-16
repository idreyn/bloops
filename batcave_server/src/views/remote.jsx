const React = require("react");
const debounce = require("debounce");

const RemoteView = React.createClass({
    componentWillMount() {
        const { remote } = this.props;
        this.handleClick = debounce(remote.triggerPulse.bind(remote), 1000);
    },

	render() {
        return <button
            onClick={this.handleClick}
            style={{
                border: 0,
                height: "100%",
                color: "black",
                fontSize: 16,
            }}
        >
            Tap anywhere to emit
        </button>
    },
});

module.exports = { RemoteView };