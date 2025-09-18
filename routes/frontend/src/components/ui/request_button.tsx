//this is a custome react hook that sends a request to the url which you give and also the body that you give 
import { use, useEffect, useState } from "react";
import axios from 'axios';

interface RequestButtonProp{
    url: string;
    body: object;
}
export function useRequest({url, body}: RequestButtonProp){
    const [loading, setloading] = useState(false);
    const [error, seterror] = useState<string | null>(null);
    const [response, setresponse] = useState<any>(null);
    const [succesfull, setSuccesfull] = useState<null | Boolean>(null);


    // send the request using axios 
    const sendRequest = async () => {
        setloading(true);
        seterror(null);
        try{
            const res = await axios.post(url, body);
            setresponse(res.data);
            setSuccesfull(true);  // this is when there is succes 
            return res.data;
        }
        catch(error: any){
            seterror(error.message);
            setSuccesfull(false); // this is when there is no succes in the request
            throw error;
        }finally{
            setloading(false);
        }
    };
    return {sendRequest, loading, error, response, succesfull}
}

