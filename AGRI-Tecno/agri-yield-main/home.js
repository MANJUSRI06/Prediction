import Chatbot from "https://cdn.n8nchatui.com/v1/embed.js";

Chatbot.init({
    n8nChatUrl: "https://teachnoverseai.app.n8n.cloud/webhook/18f87072-3bb8-4283-81b2-8a8bcd7448b9/chat",
    metadata: {},
    theme: {
        button: {
            backgroundColor: "#4caf50",
            right: 20,
            bottom: 20,
            size: 50,
            iconColor: "#373434",
            customIconSrc: "https://www.svgrepo.com/show/339963/chat-bot.svg",
            customIconSize: 60,
            customIconBorderRadius: 30
        },
        chatWindow: {
            title: "AgriCare Assistant",
            welcomeMessage: "🌱 Hello farmer! Ask me about crop diseases, fertilizers, and weather.",
            backgroundColor: "#dcf9e5",
            height: 600,
            width: 400
        }
    }
});