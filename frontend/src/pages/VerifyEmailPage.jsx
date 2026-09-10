import { useParams } from "react-router";
import { useEffect } from "react";
import post from "../functions/post";

const VerifyEmailPage = () =>{
let params = useParams();
const data = {"key":params.key}

const VerifyEmail = async(event) =>{
const response = await post({"url": "/api/auth/registration/verify-email/", "data": data});
console.log(data)
}
useEffect(()=>{
    const Verify = async () =>{
        await VerifyEmail();
    }
    Verify();
}, [])
}

export default VerifyEmailPage; 