from fastapi import FastAPI, Response
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from libcamera import controls
import io
from threading import Condition

app = FastAPI()

global counter
counter = 0

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

output = StreamingOutput()

@app.get("/stream.mjpg")
async def stream_mjpg():
    global counter
    try:
        counter += 1
        print("Current viewers:", counter)
        while True:
            with output.condition:
                output.condition.wait()
                frame = output.frame
            yield b'--FRAME\r\n'
            yield b'Content-Type: image/jpeg\r\n\r\n'
            yield frame
            yield b'\r\n'
    except Exception as e:
        counter -= 1
        print("Current viewers:", counter)
        print('Removed streaming client:', str(e))

@app.get("/status")
async def status():
    return Response(status_code=204)

@app.get("/picture")
async def picture():
    return Response(status_code=501)

if __name__ == "__main__":
    import uvicorn
    picam2 = Picamera2()
    picam2.video_configuration.controls.FrameRate = 24.0
    picam2.configure(picam2.create_video_configuration(main={"size": (600, 600)}))
    picam2.iso = 150
    picam2.set_controls({"AnalogueGain": 1.5})
    picam2.start_recording(JpegEncoder(), FileOutput(output))
    uvicorn.run(app, host="0.0.0.0", port=8000)
