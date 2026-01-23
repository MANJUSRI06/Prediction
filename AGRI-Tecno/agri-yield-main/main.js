import { initializeApp } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup }
from "https://www.gstatic.com/firebasejs/12.1.0/firebase-auth.js";
// TODO: Replace with your Firebase config
const firebaseConfig = {
    apiKey: "AIzaSyBKsdwBBfykxQUhojaI2Y9a6in16Q26Cow",
    authDomain: "app-5eeb0.firebaseapp.com",
    projectId: "app-5eeb0",
    storageBucket: "app-5eeb0.firebasestorage.app",
    messagingSenderId: "527633506292",
    appId: "1:527633506292:web:4fa6fae14acc58b5eda3a1",
    measurementId: "G-T6D35L7D5K"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

const loginBtn = document.getElementById("loginBtn");
const googleBtn = document.getElementById("btnGoogle");

// Create account button
if (loginBtn) {
    loginBtn.addEventListener("click", () => {
        localStorage.setItem("welcomeMsg", "Welcome to Agri Daingo 🌱");
        window.location.href = "home.html";
    });
}

// Google Sign-In
if (googleBtn) {
    googleBtn.addEventListener("click", () => {
        const provider = new firebase.auth.GoogleAuthProvider();
        auth.signInWithPopup(provider)
            .then((result) => {
                const user = result.user;
                localStorage.setItem("welcomeMsg", `Welcome ${user.displayName} to Agri Daingo 🌱`);
                alert(`Signed in as ${user.displayName}`);
                // Optionally redirect after login
                // window.location.href = "home.html";
            })
            .catch((error) => {
                console.error(error);
                alert("Google Sign-In failed!");
            });
    });
}