import { useParams } from "react-router";
import { useEffect, useState } from "react";
import VerifyEmail from "../functions/VerifyEmail";

const VerifyEmailPage = () =>{
let params = useParams();
const data = {"key":params.key}
const [result, setResult] = useState({status: "pending"});

useEffect(()=>{
    const Verify = async () =>{
       let value = await VerifyEmail(data);
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