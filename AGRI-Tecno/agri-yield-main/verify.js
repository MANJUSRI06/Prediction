window.onload = function() {
    // Your code here
    render()
};

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyDdhn8AWDhwFn5qW19BJbygLdGzPoosE7U",
    authDomain: "login-8b034.firebaseapp.com",
    projectId: "login-8b034",
    storageBucket: "login-8b034.appspot.com", // ✅ fixed here
    messagingSenderId: "301689381610",
    appId: "1:301689381610:web:c710d324c284de45652d93"
};

// Initialize Firebase
const app = initializeApp(firebaseCaonfig);
const auth = firebase.auth();

function render() {
    window.recaptchaver
}