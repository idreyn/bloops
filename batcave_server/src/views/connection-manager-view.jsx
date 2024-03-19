const React = require("react");
const { StyleSheet, css } = require("aphrodite");

const ErrorIcon = require("material-ui/svg-icons/alert/error.js").default;

const { ConnectionManager } = require("../connection-manager.js");
const { RemoteStatus } = require("../../protocol.js");
const { Bat } = require("./bat.jsx");

const ConnectionManagerView = React.createClass({
	propTypes: {
		connectionManager: React.PropTypes
			.instanceOf(ConnectionManager).isRequired,
	},

	renderIcon() {
		const { connectionManager } = this.props;
		switch (connectionManager.remoteStatus) {
			case RemoteStatus.CONNECTED:
			case RemoteStatus.DISCONNECTED:
				return <Bat
					className={css(styles.largeIcon, styles.ringing)}
				/>;
			case RemoteStatus.NO_SOCKET:
				return <ErrorIcon className={css(styles.largeIcon)} />;
			default:
				return null;
		}
	},

	render() {
		const { connectionManager } = this.props;
		return <div className={css(styles.outer)}>
			{this.renderIcon()}
			<span>{connectionManager.statusText()}</span>
		</div>;
	}
});

const ringKeyframes = {
	"0%": { transform: "rotate(0deg)" },
	"3%": { transform: "rotate(30deg)" },
	"6%": { transform: "rotate(-30deg)" },
	"9%": { transform: "rotate(30deg)" },
	"12%": { transform: "rotate(-30deg)" },
	"15%": { transform: "rotate(30deg)" },
	"18%": { transform: "rotate(-30deg)" },
	"21%": { transform: "rotate(30deg)" },
	"24%": { transform: "rotate(0deg)" },
};

const styles = StyleSheet.create({
	largeIcon: {
		display: "block",
		width: 150,
		height: 150,
		marginBottom: 20,
	},
	ringing: {
		animationName: [ringKeyframes],
		animationDuration: "3s",
		animationIterationCount: "infinite",
	},
	outer: {
		display: "flex",
		flexDirection: "column",
		alignItems: "center",
		height: "100%",
		justifyContent: "center",
	},
});

module.exports = { ConnectionManagerView };