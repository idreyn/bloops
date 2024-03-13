const React = require("react");
const { StyleSheet, css } = require("aphrodite");

const Slider = require("material-ui/Slider").default;
const Dialog = require("material-ui/Dialog").default;
const FlatButton = require("material-ui/FlatButton").default;
const { Card } = require("material-ui/Card");

const LabeledSlider = React.createClass({
	propTypes: {
		getLabel: React.PropTypes.func.isRequired,
		onDragStart: React.PropTypes.func,
		onDragEnd: React.PropTypes.func,
		onUpdate: React.PropTypes.func,
		value: React.PropTypes.number,
	},

	getInitialState() {
		return {
			dragging: false,
			dragValue: this.props.value
		};
	},

	handleDragStart(e) {
		const { onDragStart } = this.props;
		this.setState({
			dragging: true,
			dragValue: this.props.value,
		});
		onDragStart && onDragStart(e);
	},

	handleDragStop(e) {
		const { onDragStop, onUpdate } = this.props;
		this.setState({ dragging: false });
		onDragStop && onDragStop(e);
		onUpdate && onUpdate(this.state.dragValue);
	},

	handleChange(e, value) {
		if (this.state.dragging) {
			this.setState({ dragValue: value });
		}
	},

	render() {
		const { getLabel, value, onUpdate, ...rest } = this.props;
		const { dragging, dragValue } = this.state;
		const currentValue = dragging ? dragValue : value;
		return <div style={{ margin: 0 }}>
			<label>
				<span>{getLabel(currentValue)}</span>
				<Slider
					{...rest}
					onDragStart={this.handleDragStart}
					onDragStop={this.handleDragStop}
					onChange={this.handleChange}
					sliderStyle={{ margin: 0 }}
					value={currentValue}
				/>
			</label>
		</div>;
	}
});

const ConfirmDialog = React.createClass({
	propTypes: {
		title: React.PropTypes.string.isRequired,
		text: React.PropTypes.string.isRequired,
		onCancel: React.PropTypes.func.isRequired,
		onConfirm: React.PropTypes.func.isRequired,
		open: React.PropTypes.bool.isRequired,
	},

	render() {
		const { title, text, onCancel, onConfirm, open } = this.props;
		return <Dialog
			title={title}
			modal={true}
			open={open}
			actions={[
				<FlatButton
					label="No"
					primary={true}
					onTouchTap={onCancel}
					keyboardFocused={true}
				/>,
				<FlatButton
					label="Yes"
					primary={true}
					onTouchTap={onConfirm}
				/>
			]}
		>{text}</Dialog>;
	},
});

const RobinCard = React.createClass({
	render() {
		return <Card style={{ marginTop: 10 }} {...this.props} />;
	}
});

const ShrugView = React.createClass({
	render() {
		return <div
			style={{
				display: "flex",
				alignItems: "center",
				justifyContent: "center",
				flexDirection: "column",
				height: "100%",
			}}
		>
			<div style={{ fontSize: 30 }}>
				{"¯\\_(ツ)_/¯"}
			</div>
			<div>Not implemented yet</div>
		</div>
	},
});

module.exports = { LabeledSlider, RobinCard, ConfirmDialog, ShrugView };