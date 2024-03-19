const express = require("express");
const { Server } = require("socket.io");

const { DeviceStatus, Message, DirectMessage } = require("./protocol.js");
const { HOST, PORT } = require("./config.js");

const app = express();
const http = app.listen(PORT, HOST);
const io = new Server(http, { maxHttpBufferSize: 10 * 1024 ** 1024 });
app.use(express.static(__dirname));

class Device {
	constructor(socket, info) {
		this.socket = socket;
		this.info = info;
		this.id = info.id;
		this.status = DeviceStatus.UNKNOWN;
	}
}

class Remote {
	constructor(socket) {
		this.socket = socket;
	}
}

const devices = new Set();
const remotes = new Set();

io.on("connection", (socket) => {
	socket.on(Message.HANDSHAKE_DEVICE, (info) => createDeviceSocket(socket, info));
	socket.on(Message.HANDSHAKE_REMOTE, () => createRemoteSocket(socket));
});

const createDeviceSocket = (socket, info) => {
	const device = new Device(socket, info);
	devices.add(device);
	device.socket.on(Message.DISCONNECT, (e) => {
		device.socket.removeAllListeners();
		devices.delete(device);
	});
	device.socket.on(Message.AUDIO, (audio) => {
		remotes.forEach(remote => remote.socket.emit(Message.AUDIO, audio));
	});
};

const createRemoteSocket = (socket) => {
	let device = null;
	const remote = new Remote(socket);
	remotes.add(remote);

	setInterval(() => {
		if (!device) {
			socket.emit(
				Message.DEVICE_LISTING,
				Array.from(devices, d => d.info)
			);
		}
	}, 1000);

	remote.socket.on(Message.CHOOSE_DEVICE, (idChoice) => {
		const chosenDevice = Array.from(devices).filter(d => d.id === idChoice)[0];
		if (!chosenDevice) {
			remote.socket.emit(Message.DEVICE_CHOICE_INVALID, idChoice);
		} else {
			device = chosenDevice;
			device.socket.on(Message.DISCONNECT, () => {
				remote.socket.emit(Message.DEVICE_STATUS, {
					status: DeviceStatus.DISCONNECTED,
				});
			});
			remote.socket.on(Message.DISCONNECT, () => {
				device && device.socket.emit(Message.DEVICE_REMOTE_DISCONNECT);
			});
			setupDirectMessaging(remote, chosenDevice);
			device.socket.emit(Message.DEVICE_REMOTE_CONNECT);
			remote.socket.emit(Message.DEVICE_CHOICE_SUCCESSFUL, idChoice);
		}
	});
	socket.on(Message.DISCONNECT, () => {
		remote.socket.removeAllListeners();
		remotes.delete(remote);
	});
};

const setupDirectMessaging = (remote, device) => {
	Object.values(DirectMessage).forEach(messageType => {
		const onMessageFromRemote = (...args) => {
			device.socket.emit(messageType, ...args);
		};
		const onMessageFromDevice = (...args) => {
			if (messageType !== Message.AUDIO) {
				remote.socket.emit(messageType, ...args);
			}
		};
		device.socket.on(messageType, onMessageFromDevice);
		device.socket.on(Message.DISCONNECT, () => remote.socket.off(messageType, onMessageFromRemote));
		remote.socket.on(messageType, onMessageFromRemote);
		remote.socket.on(Message.DISCONNECT, () => device.socket.off(messageType, onMessageFromDevice));
	});
}