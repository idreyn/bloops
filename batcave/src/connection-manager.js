const { RemoteStatus, DeviceStatus, Message } = require("../protocol.js");

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
			backend.emit(Message.HANDSHAKE_REMOTE);
		}
		this.update();
	}

	statusText() {
		return {
			[RemoteStatus.DISCONNECTED]: "Waiting for a device..." +
				this.deviceListing.length.toString() + " found so far.",
			[RemoteStatus.NO_SOCKET]: "Socket unavailable." +
				" Is the server running?",
		}[this.remoteStatus] || "Uh-oh";
	}

	onDeviceListing(listing) {
		this.deviceListing = listing;
		if (listing.length > 0 && this.autoConnectToFirstClient) {
			this.backend.emit(Message.CHOOSE_DEVICE, listing[0].id);
		}
		this.update();
	}

	onDeviceStatus(status) {
		this.deviceStatus = status;
		if (status === DeviceStatus.DISCONNECTED) {
			this.remoteStatus = RemoteStatus.DISCONNECTED;
		}
		this.update();
	}

	onReceiveAudio({ audio }) {
		playWavAudio(audio);
	}
}

module.exports = { ConnectionManager };