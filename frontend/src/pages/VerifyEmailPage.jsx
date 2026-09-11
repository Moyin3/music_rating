import { useParams } from "react-router";
import { useEffect, useState } from "react";
import post from "../functions/post";

const VerifyEmailPage = () =>{
let params = useParams();
const data = {"key":params.key}
const [result, setResult] = useState(false);


const VerifyEmail = async(event) =>{
const response = await post({"url": "/api/auth/registration/verify-email/", "data": data});
console.log(data)
console.log("What is happening to verification", response);
return response;
}
useEffect(()=>{
    const Verify = async () =>{
       let value = await VerifyEmail();
        setResult(value);
    }
    Verify();
}, [])
return(
    result.status == "success" &&(
        <h1>Email Verified</h1>
    )
)
}

export default VerifyEmailPage; 