const debounce = require("debounce");

const React = require("react");
const { StyleSheet, css } = require("aphrodite");

const FlatButton = require("material-ui/FlatButton").default;
const IconButton = require("material-ui/IconButton").default;
const FAB = require("material-ui/FloatingActionButton").default;
const Paper = require("material-ui/Paper").default;
const Toggle = require("material-ui/Toggle").default;
const Subheader = require("material-ui/Subheader").default;
const { List, ListItem } = require("material-ui/List");
const { Tab, Tabs } = require("material-ui/Tabs");
const { Card, CardActions, CardHeader, CardText } = require("material-ui/Card");
const IconMenu = require("material-ui/IconMenu").default;
const MenuItem = require("material-ui/MenuItem").default;
const TextField = require("material-ui/TextField").default;

const PlayIcon = require("material-ui/svg-icons/av/play-arrow.js").default;
const RestartIcon = require("material-ui/svg-icons/navigation/refresh.js").default;
const PowerIcon = require("material-ui/svg-icons/action/power-settings-new.js").default;
const UndoIcon = require("material-ui/svg-icons/content/undo.js").default;
const RedoIcon = require("material-ui/svg-icons/content/redo.js").default;
const GamepadIcon = require("material-ui/svg-icons/hardware/gamepad.js").default;
const LabelIcon = require("material-ui/svg-icons/action/label.js").default;
const LabelIconOutline = require("material-ui/svg-icons/action/label-outline.js").default;

const { Remote } = require("../remote.js");
const { Pulse } = require("../models.js");

const { LabeledSlider, RobinCard, ConfirmDialog } = require("./shared.jsx");

const ConfigView = React.createClass({
	propTypes: {
		remote: React.PropTypes.instanceOf(Remote).isRequired,
	},

	render() {
		const { remote } = this.props;
		return <div>
			<PulseControl {...this.props} />
			{remote.device && <DeviceInfo {...this.props} />}
			<FAB
				onTouchTap={debounce(remote.triggerPulse.bind(remote), 1000)}
				secondary
				style={{
					position: "fixed",
					bottom: 75,
					right: 20,
					zIndex: 1,
				}}
			>
				<PlayIcon />
			</FAB>
		</div>;
	},
});

const DeviceInfo = React.createClass({
	getInitialState() {
		return {
			confirmingRestart: false,
			confirmingReboot: false,
		};
	},

	render() {
		const { remote } = this.props;
		const { confirmingRestart, confirmingReboot } = this.state;
		return <RobinCard>
			<List>
				<Subheader>Device information</Subheader>
				<ListItem
					disabled
					primaryText="Identifier"
					secondaryText={remote.device.id}
				/>
				<ListItem
					disabled
					primaryText="IP address"
					secondaryText={remote.device.ip}
				/>
				<ListItem
					disabled
					primaryText="Bluetooth connections"
					secondaryText={remote.device.bluetoothConnections}
				/>
				<ListItem
					disabled
					primaryText="Last seen"
					secondaryText={remote.device.lastSeen}
				/>
				<ListItem
					disabled
					primaryText="Device battery"
					secondaryText={
						remote.device.deviceBatteryLow ? "Low" : "Okay"
					}
				/>
				<ListItem
					disabled
					primaryText="Emitter battery"
					secondaryText={
						remote.device.emitterBatteryLow ? "Low" : "Okay"
					}
				/>
				<Subheader>Debugging overrides</Subheader>
				<ListItem
					primaryText="Force-enable emitters"
					secondaryText="Useful for debugging the analog hardware"
					rightToggle={<Toggle
						toggled={remote.overrides.forceEnableEmitters}
						onToggle={
							(e, forceEnableEmitters) => remote.updateOverrides({
								forceEnableEmitters
							})
						}
					/>}
				/>
				<ListItem
					primaryText="Disable device playback"
					secondaryText="Turns off playback through headphone jack"
					rightToggle={<Toggle
						toggled={remote.overrides.disablePlayback}
						onToggle={
							(e, disablePlayback) => remote.updateOverrides({
								echolocation: {
									playback: !disablePlayback,
								}
							})
						}
					/>}
				/>
				<Subheader>Here be dragons</Subheader>
				<ListItem
					primaryText="Restart the device server"
					secondaryText={"You'll lose connection" +
						" for at least a few seconds."
					}
					rightIcon={<RestartIcon />}
					onTouchTap={() => this.setState({
						confirmingRestart: true,
					})}
				/>
				<ListItem
					primaryText="Restart the device"
					secondaryText="All bets are off"
					rightIcon={<PowerIcon />}
					onTouchTap={() => this.setState({
						confirmingReboot: true,
					})}
				/>
			</List>
			<ConfirmDialog
				title="Really restart the server?"
				text="This will take a few seconds."
				open={confirmingRestart}
				onConfirm={() => {
					this.setState({ confirmingRestart: false });
				}}
				onCancel={() => this.setState({ confirmingRestart: false })}
			/>
			<ConfirmDialog
				title="Really restart the device?"
				text="This will probably be annoying."
				open={confirmingReboot}
				onConfirm={() => {
					this.setState({ confirmingReboot: false });
				}}
				onCancel={() => this.setState({ confirmingReboot: false })}
			/>
		</RobinCard>;
	},
});

const PulseControl = React.createClass({
	getInitialState() {
		return {
			editingLabelText: null,
			showLabelField: false,
			labelText: this.props.remote.config.save.file_prefix || "",
		}
	},

	handlePulseUpdate(updated) {
		const { remote } = this.props;
		remote.updatePulse(updated);
	},

	handleToggleLabelField() {
		const { remote } = this.props;
		let { showLabelField, labelText } = this.state;
		remote.updateLabel(showLabelField ? "" : labelText);
		this.setState({ showLabelField: !showLabelField });
	},

	handleLabelFocus(e) {
		this.setState({ editingLabelText: this.state.labelText });
	},

	handleLabelChange(e) {
		this.setState({
			editingLabelText: e.target.value
				.split(" ")
				.map((bit) => bit
					.split("")
					.filter((char) => /^[A-Za-z0-9\-]/.test(char))
					.join(""))
				.join("-")
		});
	},

	handleLabelBlur(e) {
		const { remote } = this.props;
		const labelText = e.target.value;
		remote.updateLabel(labelText);
		this.setState({ labelText, editingLabelText: null });
	},

	renderInner() {
		const { remote } = this.props;
		const { showLabelField, editingLabelText, labelText } = this.state;
		const pulse = remote.config.pulse;
		return <List style={{ padding: 0 }}>
			<ListItem disabled>
				<LabeledSlider
					name="duration"
					getLabel={(n) => <span>Duration: {Math.round(n)}ms</span>}
					onUpdate={(v) => this.handlePulseUpdate({ ms_duration: v })}
					min={1}
					max={20}
					step={1}
					value={pulse.ms_duration}
				/>
			</ListItem>
			{pulse.kind === Pulse.kinds.TONE && <ListItem disabled>
				<LabeledSlider
					name="freq"
					getLabel={(n) =>
						<span>Frequency: {n}kHz</span>
					}
					onUpdate={(v) => this.handlePulseUpdate({ khz_freq: v })}
					min={10}
					max={90}
					step={5}
					value={pulse.khz_freq}
				/>
			</ListItem>}
			{pulse.kind === Pulse.kinds.CHIRP && <ListItem disabled>
				<LabeledSlider
					name="start-freq"
					getLabel={(n) =>
						<span>Starting frequency: {n}kHz</span>
					}
					onUpdate={(v) => this.handlePulseUpdate({ khz_start: v })}
					min={10}
					max={90}
					step={5}
					value={pulse.khz_start}
				/>
			</ListItem>}
			{pulse.kind === Pulse.kinds.CHIRP && <ListItem disabled>
				<LabeledSlider
					name="end-freq"
					getLabel={(n) =>
						<span>Ending frequency: {n}kHz</span>
					}
					onUpdate={(v) => this.handlePulseUpdate({ khz_end: v })}
					min={10}
					max={90}
					step={5}
					value={pulse.khz_end}
				/>
			</ListItem>}
			<ListItem disabled>
				<LabeledSlider
					name="slowdown"
					getLabel={(n) =>
						<span>Slowdown factor: {n}</span>
					}
					onUpdate={(slowdown) => remote.updateConfig({ echolocation: { slowdown } })}
					min={5}
					max={50}
					step={1}
					value={remote.config.echolocation.slowdown}
				/>
			</ListItem>
			<ListItem disabled>
				<LabeledSlider
					name="record-duration"
					getLabel={(n) =>
						<span>Recording duration: {n}ms</span>
					}
					onUpdate={(ms_record_duration) => remote.updateConfig({ echolocation: { ms_record_duration } })}
					min={20}
					max={200}
					step={5}
					value={remote.config.echolocation.ms_record_duration}
				/>
			</ListItem>
			{pulse.kind !== Pulse.kinds.NOISE && <ListItem
				primaryText="Square"
				secondaryText="Emit a square wave"
				rightToggle={<Toggle
					toggled={pulse.square}
					onToggle={(e, v) => this.handlePulseUpdate({ square: v })}
				/>}
			/>}
			{pulse.kind === Pulse.kinds.CHIRP && <ListItem
				primaryText="Logarithmic"
				secondaryText="Chirp with a logarithmic freqency sweep"
				rightToggle={<Toggle
					toggled={pulse.logarithmic}
					onToggle={(e, v) => this.handlePulseUpdate({ logarithmic: v })}
				/>}
			/>}
			<ListItem
				primaryText="Enable side emitters"
				secondaryText="If disabled, only the front will be used"
				rightToggle={<Toggle
					toggled={remote.config.echolocation.emitters.side_gain === 1}
					onToggle={
						(e, enabled) => remote.updateConfig({
							echolocation: {
								emitters: {
									side_gain: enabled ? 1 : 0,
								}
							}
						})
					}
				/>}
			/>
			{showLabelField && <ListItem style={{ paddingTop: 0 }}>
				<TextField
					style={{ padding: 0, margin: 0, width: "100%" }}
					hintText="Label for .wav files"
					onFocus={this.handleLabelFocus}
					onChange={this.handleLabelChange}
					onBlur={this.handleLabelBlur}
					value={editingLabelText ?? labelText}
				/>
			</ListItem>}
		</List>;
	},

	render() {
		const { remote } = this.props;
		const { showLabelField } = this.state;
		const pulse = remote.config.pulse;
		return <RobinCard>
			<Tabs
				value={pulse.kind}
				onChange={(v) => this.handlePulseUpdate({ kind: v })}
			>
				<Tab value={Pulse.kinds.TONE} label="Tone" />
				<Tab value={Pulse.kinds.CHIRP} label="Chirp" />
				<Tab value={Pulse.kinds.NOISE} label="Noise" />
			</Tabs>
			<div
				style={{
					display: "flex",
					justifyContent: "space-around",
				}}
			>
				<IconButton
					disabled={remote.pulseHistory.atStart()}
					onTouchTap={() => remote.pulseHistory.undo()}
				><UndoIcon />
				</IconButton>
				<IconButton
					disabled={remote.pulseHistory.atEnd()}
					onTouchTap={() => remote.pulseHistory.redo()}
				>
					<RedoIcon />
				</IconButton>
				<IconMenu
					iconButtonElement={<IconButton>
						<GamepadIcon />
					</IconButton>}
				>
					<Subheader>Assign this pulse to a button</Subheader>
					{Object.keys(remote.physicalButtons).map(
						(k) => <MenuItem
							key={k}
							onTouchTap={() => remote.assignPulseToButton(
								k, remote.config.pulse
							)}
						>
							{remote.physicalButtons[k]}
						</MenuItem>
					)}
				</IconMenu>
				<IconButton onTouchTap={this.handleToggleLabelField}>
					{showLabelField ? <LabelIcon /> : <LabelIconOutline />}
				</IconButton>
			</div>
			{this.renderInner()}
		</RobinCard>;
	}
});

module.exports = { ConfigView, DeviceInfo, PulseControl };