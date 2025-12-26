#!/usr/bin/env python3
import argparse
import json
import logging
import uuid

import websockets

from protocols import MsgType, full_client_request, receive_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_cluster(voice: str) -> str:
    if voice.startswith("S_"):
        return "volcano_icl"
    return "volcano_tts"


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--appid", required=True, help="APP ID")
    parser.add_argument("--access_token", required=True, help="Access Token")
    parser.add_argument("--voice_type", required=True, help="Voice type")
    parser.add_argument("--cluster", default="", help="Cluster name")
    parser.add_argument("--text", required=True, help="Text to convert")
    parser.add_argument("--encoding", default="wav", help="Output file encoding")
    parser.add_argument(
        "--endpoint",
        default="wss://openspeech.bytedance.com/api/v1/tts/ws_binary",
        help="WebSocket endpoint URL",
    )

    args = parser.parse_args()

    # Determine cluster
    cluster = args.cluster if args.cluster else get_cluster(args.voice_type)

    # Connect to server
    headers = {
        "Authorization": f"Bearer;{args.access_token}",
    }

    logger.info(f"Connecting to {args.endpoint} with headers: {headers}")
    websocket = await websockets.connect(
        args.endpoint, additional_headers=headers, max_size=10 * 1024 * 1024
    )
    logger.info(
        f"Connected to WebSocket server, Logid: {websocket.response.headers['x-tt-logid']}",
    )

    try:
        # Prepare request payload
        request = {
            "app": {
                "appid": args.appid,
                "token": args.access_token,
                "cluster": cluster,
            },
            "user": {
                "uid": str(uuid.uuid4()),
            },
            "audio": {
                "voice_type": args.voice_type,
                "encoding": args.encoding,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": args.text,
                "operation": "submit",
                "with_timestamp": "1",
                "extra_param": json.dumps(
                    {
                        "disable_markdown_filter": False,
                    }
                ),
            },
        }

        # Send request
        await full_client_request(websocket, json.dumps(request).encode())

        # Receive audio data
        audio_data = bytearray()
        while True:
            msg = await receive_message(websocket)

            if msg.type == MsgType.FrontEndResultServer:
                continue
            elif msg.type == MsgType.AudioOnlyServer:
                audio_data.extend(msg.payload)
                if msg.sequence < 0:  # Last message
                    break
            else:
                # 更详细的错误信息
                error_info = f"TTS conversion failed: {msg}"
                if msg.type == MsgType.Error:
                    if msg.payload:
                        try:
                            error_data = json.loads(msg.payload.decode('utf-8'))
                            if 'message' in error_data:
                                error_info += f"\n错误详情: {error_data['message']}"
                            if 'code' in error_data:
                                error_info += f"\nHTTP状态码: {error_data['code']}"
                            if error_data.get('code') == 401:
                                error_info += "\n提示: 请检查 access_token 和 appid 是否正确，或 token 是否已过期"
                        except:
                            pass
                    if msg.error_code:
                        error_info += f"\n错误代码: {msg.error_code}"
                raise RuntimeError(error_info)

        # Check if we received any audio data
        if not audio_data:
            raise RuntimeError("No audio data received")

        # Save audio file
        filename = f"{args.voice_type}.{args.encoding}"
        with open(filename, "wb") as f:
            f.write(audio_data)
        logger.info(f"Audio received: {len(audio_data)}, saved to {filename}")

    finally:
        await websocket.close()
        logger.info("Connection closed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
