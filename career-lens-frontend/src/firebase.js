// Firebase Web App SDK configuration
import { initializeApp } from "firebase/app";

export const firebaseConfig = {
  apiKey: "AIzaSyDyVyROxQtHUevLFw0mtBs5hr8WeXojAkk",
  authDomain: "careerlens-7dc8c.firebaseapp.com",
  projectId: "careerlens-7dc8c",
  storageBucket: "careerlens-7dc8c.firebasestorage.app",
  messagingSenderId: "1095416671084",
  appId: "1:1095416671084:web:0ca2e04c6c1ce43668a149"
};

// Initialize Firebase Client App
export const app = initializeApp(firebaseConfig);
export default app;

