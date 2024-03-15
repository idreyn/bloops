const { WaveFile } = require('wavefile');

function slowAudioWithSincResampling(audioData, samplerate, slowdown) {
    const input = new Int16Array(audioData);
    const outputLength = input.length * slowdown;
    const output = new Int16Array(outputLength);
    function sinc(x) {
        return x === 0 ? 1 : Math.sin(Math.PI * x) / (Math.PI * x);
    }
    const windowSize = 16;
    for (let i = 0; i < outputLength; i += 2) {
        let sumL = 0;
        let sumR = 0;
        const inputPos = i / slowdown;
        for (let j = -windowSize; j <= windowSize; j++) {
            const inputIndex = inputPos + j * 2;
            if (inputIndex >= 0 && inputIndex < input.length - 1) {
                // Left channel
                sumL += sinc(j) * input[inputIndex];
                // Right channel
                sumR += sinc(j) * input[inputIndex + 1];
            }
        }
        output[i] = sumL;
        output[i + 1] = sumR;
    }
    const wav = new WaveFile();
    wav.fromScratch(2, samplerate, '16', output);
    return wav.toBuffer().buffer;
}


function slowAudio(audioData, samplerate, slowdown) {
    const input = new Int16Array(audioData);
    const output = new Int16Array(input.length * slowdown);
    for (let i = 0; i < input.length; i += 2) {
        const baseOffset = i * slowdown;
        for (let repeat = 0; repeat < slowdown; ++repeat) {
            const offset = baseOffset + repeat * 2;
            output[offset] = input[i];
            output[offset + 1] = input[i + 1];
        }
    }
    const wav = new WaveFile();
    wav.fromScratch(2, samplerate, '16', output);
    return wav.toBuffer().buffer;
}

async function playWavAudio(audioData, samplerate, slowdown) {
    const slowedAudioData = slowAudio(audioData, samplerate, slowdown);;
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const audioBuffer = await audioContext.decodeAudioData(slowedAudioData);
    const source = audioContext.createBufferSource();

    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start(0);
}

module.exports = { playWavAudio };
