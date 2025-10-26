import { set } from "react-hook-form";
import { Input } from "./input";
import { useState, type HtmlHTMLAttributes } from "react";
export function useInput(initialValue: string= ""){
    const [textInput , settextInput] = useState(""); //making the variable in which i am storing the value of the text using useState
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>)=> {
        settextInput(e.target.value);                // setting the value of the input in the settextinput variable
    };
    const reset = () => settextInput(initialValue);
    return{
        textInput,
        settextInput, 
        reset,
        onChnage: handleChange,
    };

}