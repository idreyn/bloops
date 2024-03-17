const React = require("react");
const { StyleSheet, css } = require("aphrodite");

const RemoteIcon = require("material-ui/svg-icons/action/settings-remote.js").default;
const ConfigIcon = require("material-ui/svg-icons/action/settings-applications.js").default;
const LogsIcon = require("material-ui/svg-icons/action/assignment.js").default;

const {
	BottomNavigation,
	BottomNavigationItem
} = require("material-ui/BottomNavigation");

const Paper = require("material-ui/Paper").default;

const { ConnectionManager } = require("../connection-manager.js");
const { Remote } = require("../remote.js");
const { Device, Pulse } = require("../models.js");
const { RemoteStatus, DeviceStatus } = require("../../protocol.js");

const { ShrugView } = require("./shared.jsx");
const { ConfigView } = require("./config.jsx");
const { RemoteView } = require("./remote.jsx");
const { LogsView, LogView } = require("./log-view.jsx");
const { ConnectionManagerView } = require("./connection-manager-view.jsx");

const RobinApp = React.createClass({
	propTypes: {
		remote: React.PropTypes.instanceOf(Remote).isRequired,
		connectionManager: React.PropTypes
			.instanceOf(ConnectionManager).isRequired,
	},

	getInitialState() {
		return {
			activeTab: window.localStorage.activeTab ? parseInt(window.localStorage.activeTab) : 0,
		};
	},

	setActiveTab(activeTab) {
		this.setState({ activeTab });
	},

	componentDidUpdate() {
		window.localStorage.activeTab = this.state.activeTab.toString();
	},

	renderActiveTab() {
		const { activeTab } = this.state;
		if (activeTab === 0) {
			return <RemoteView remote={this.props.remote} />
		}
		if (activeTab === 1) {
			return <ConfigView remote={this.props.remote} />;
		}
		if (activeTab === 2) {
			return <LogView remote={this.props.remote} />;
		}
		return <ShrugView />;
	},

	render() {
		const { connectionManager } = this.props;
		const { activeTab } = this.state;
		if (connectionManager.deviceStatus === DeviceStatus.DISCONNECTED) {
			return <ConnectionManagerView {...this.props} />
		}
		return <div className={css(styles.outer)}>
			<div className={css(styles.content)}>
				{this.renderActiveTab()}
			</div>
			<Paper zDepth={1} className={css(styles.navigation)}>
				<BottomNavigation selectedIndex={activeTab}>
					<BottomNavigationItem
						label="Remote"
						icon={<RemoteIcon />}
						onTouchTap={() => this.setActiveTab(0)}
					/>
					<BottomNavigationItem
						label="Config"
						icon={<ConfigIcon />}
						onTouchTap={() => this.setActiveTab(1)}
					/>
					<BottomNavigationItem
						label="Logs"
						icon={<LogsIcon />}
						onTouchTap={() => this.setActiveTab(2)}
					/>
				</BottomNavigation>
			</Paper>
		</div>;
	}
});

const styles = StyleSheet.create({
	content: {
		display: "flex",
		flexDirection: "column",
		flex: 1,
		overflowY: "scroll",
		margin: "0 auto",
		paddingBottom: 10,
		width: "95%",
	},
	navigation: {
		alignSelf: "flex-end",
		zIndex: 99999,
		width: "100%",
	},
	outer: {
		display: "flex",
		flexDirection: "column",
		height: "100%",
		maxHeight: "100%",
	},
});

module.exports = { RobinApp };