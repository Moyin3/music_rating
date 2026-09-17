import { useParams } from "react-router";
import { useEffect, useState, useRef } from "react";
import VerifyEmail from "../functions/VerifyEmail";
import NavigationBar from "../components/Navigationbar";

const VerifyEmailPage = () =>{
let params = useParams();
const data = {"key":params.key}
const [result, setResult] = useState({status: "pending"});
const calledRef = useRef(false);

useEffect(()=>{
    const Verify = async () =>{
       let value = await VerifyEmail(data);
        setResult(value);
    }
    if (calledRef.current) return;
    calledRef.current = true;
    Verify();
}, [])
return(
    <>
    <NavigationBar />
    {result.status === "success" &&(
        <h1>Email Verified</h1>
    )}
    </>
)
}

export default VerifyEmailPage; 