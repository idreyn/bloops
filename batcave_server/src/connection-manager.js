const { RemoteStatus, DeviceStatus, Message } = require("../protocol.js");
const { playWavAudio } = require("./audio.js");

class ConnectionManager {
	constructor(update, backend) {
		this.update = update;
		this.backend = backend;
		this.deviceListing = [];
		this.autoConnectToFirstClient = true;
		this.remoteStatus = backend.hasSocket ?
			RemoteStatus.DISCONNECTED :
			RemoteStatus.NO_SOCKET;
		this.deviceStatus = DeviceStatus.DISCONNECTED;
		if (backend.hasSocket) {
			backend.on(
				Message.DEVICE_LISTING,
				this.onDeviceListing.bind(this)
			);
			backend.on(
				Message.DEVICE_STATUS,
				this.onDeviceStatus.bind(this)
			);
			backend.on(
				Message.DEVICE_CHOICE_INVALID,
				(id) => console.warn(`${id} is an invalid device ID.`)
			);
			backend.on(
				Message.DEVICE_CHOICE_SUCCESSFUL,
				(id) => console.info(`${id} was chosen successfully.`)
			);
			backend.on(
				Message.AUDIO,
				this.onReceiveAudio.bind(this),
			);
			backend.on(Message.CONNECT, this.onRemoteConnect.bind(this));
			backend.on(Message.DISCONNECT, this.onRemoteDisconnect.bind(this));
		}
		this.update();
	}

	statusText() {
		if (this.remoteStatus === RemoteStatus.CONNECTED) {
			return "Waiting for a device..." +
				this.deviceListing.length.toString() + " found so far.";
		}
		if (this.remoteStatus === RemoteStatus.DISCONNECTED) {
			return "Looking for Batcave server...";
		}
		return "Socket unavailable. Is the server running?";
	}

	onRemoteConnect() {
		if (this.remoteStatus !== this.remoteStatus.CONNECTED) {
			backend.emit(Message.HANDSHAKE_REMOTE);
		}
		this.remoteStatus = RemoteStatus.CONNECTED;
		this.update();
	}

	onRemoteDisconnect() {
		this.deviceStatus = DeviceStatus.DISCONNECTED;
		this.remoteStatus = RemoteStatus.DISCONNECTED;
		this.deviceListing = [];
		this.update();
	}

	onDeviceListing(listing) {
		this.deviceListing = listing;
		if (listing.length > 0 && this.autoConnectToFirstClient) {
			this.backend.emit(Message.CHOOSE_DEVICE, listing[0].id);
		}
		this.update();
	}

	onDeviceStatus({ status }) {
		this.deviceStatus = status;
		this.update();
	}

	onReceiveAudio({ audio, samplerate, slowdown }) {
		playWavAudio(audio, samplerate, slowdown);
	}
}

module.exports = { ConnectionManager };