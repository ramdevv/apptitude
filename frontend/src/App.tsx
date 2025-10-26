import { Card, CardContent } from "@/components/ui/card";
import { APITester } from "./APITester";
import "./index.css";

import logo from "./logo.svg";
import reactLogo from "./react.svg";
import { Login } from "./components/ui/login";
import { MenubarDemo } from "./components/ui/MenueBar";
import { Register } from "./components/ui/register";
import { Routes, Route } from "react-router-dom";
import { UploadResume } from "./components/ui/UploadResume";
import { QuizDetails } from "./components/ui/quizDetails";


export function App() {
  return (
    <div className="flex justify-center items-center h-screen">
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path = "/Register" element = {<Register />} />
        <Route path = "/UploadResume" element = {<UploadResume />} />
        <Route path = "/menubar" element = {<MenubarDemo />} />
        <Route path = "/quizDetails" element = {<QuizDetails/>} />

      </Routes>
      
    </div>
  );
}

export default App;