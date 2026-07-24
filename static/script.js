/*  =========================================================
    LAN Chat – Client Script
    Handles WebSocket connection, reconnection, heartbeat,
    and message rendering.
    ========================================================= */

(function () {
    "use strict";

    // ---- DOM refs ----
    const messagesDiv  = document.getElementById("messages");
    const messageInput = document.getElementById("message-input");
    const sendBtn      = document.getElementById("send-btn");

    // ---- State ----
    let ws = null;
    let heartbeatTimer = null;
    let reconnectTimer = null;
    const HEARTBEAT_INTERVAL_MS = 15000;   // 15 s
    const RECONNECT_DELAY_MS    = 2000;    // 2 s

    // ==================================================================
    // WebSocket
    // ==================================================================

    function wsUrl() {
        const proto = location.protocol === "https:" ? "wss:" : "ws:";
        return proto + "//" + location.host + "/ws";
    }

    function connectWebSocket() {
        if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
            return;
        }

        ws = new WebSocket(wsUrl());

        ws.addEventListener("open", function () {
            startHeartbeat();
        });

        ws.addEventListener("message", function (event) {
            let data;
            try {
                data = JSON.parse(event.data);
            } catch (_) {
                return;
            }

            // Ignore pong responses
            if (data.type === "pong") return;

            renderMessage(data);
        });

        ws.addEventListener("close", function () {
            stopHeartbeat();
            scheduleReconnect();
        });

        ws.addEventListener("error", function () {
            // The close event will fire right after, which triggers reconnect.
        });
    }

    // ==================================================================
    // Heartbeat
    // ==================================================================

    function startHeartbeat() {
        stopHeartbeat();
        heartbeatTimer = setInterval(function () {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: "ping" }));
            }
        }, HEARTBEAT_INTERVAL_MS);
    }

    function stopHeartbeat() {
        if (heartbeatTimer) {
            clearInterval(heartbeatTimer);
            heartbeatTimer = null;
        }
    }

    // ==================================================================
    // Reconnection
    // ==================================================================

    function scheduleReconnect() {
        if (reconnectTimer) return;
        reconnectTimer = setTimeout(function () {
            reconnectTimer = null;
            connectWebSocket();
        }, RECONNECT_DELAY_MS);
    }

    // ==================================================================
    // Sending messages
    // ==================================================================

    function sendMessage() {
        var text = messageInput.value.trimEnd();
        if (!text) return;
        if (!ws || ws.readyState !== WebSocket.OPEN) return;

        ws.send(JSON.stringify({
            type: "message",
            text: text
        }));

        messageInput.value = "";
        messageInput.focus();
    }

    sendBtn.addEventListener("click", sendMessage);

    messageInput.addEventListener("keydown", function (e) {
        // Enter → send, Shift+Enter → newline
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // ==================================================================
    // Rendering
    // ==================================================================

    function renderMessage(data) {
        var div = document.createElement("div");
        div.classList.add("msg");

        // Timestamp line
        if (data.timestamp) {
            var ts = document.createElement("div");
            ts.classList.add("timestamp");
            ts.textContent = data.timestamp;
            div.appendChild(ts);
        }

        // Message text
        var textDiv = document.createElement("div");
        textDiv.classList.add("text");
        textDiv.textContent = data.text || "";
        div.appendChild(textDiv);

        messagesDiv.appendChild(div);

        // Auto-scroll to bottom
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // ==================================================================
    // Auto-connect on page load
    // ==================================================================
    connectWebSocket();
    messageInput.focus();
})();
