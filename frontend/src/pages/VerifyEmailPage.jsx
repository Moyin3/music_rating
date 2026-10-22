import { useParams } from "react-router";
import { useEffect, useState, useRef } from "react";
import VerifyEmail from "../functions/VerifyEmail";
import NavigationBar from "../components/Navigationbar";
import styles from "./styles/VerifyEmailPage.module.css";
import LoginButton from "../components/LoginButton";

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
    /* This was put it stop the double request that was happening */
    if (calledRef.current) return;
    calledRef.current = true;
    Verify();
}, [])
return(
    <>
    <NavigationBar />
    <main className={styles.main}>
        <div className = {styles.verifyDiv}>
    {result.status === "pending" &&(
        <div className={styles.pending}>
            pending...
        </div>
    )}
    {result.status === "success" &&(
        <>
        <h1 className = {styles.emailVerified}>Email Verified</h1>
        <LoginButton />
        </>
    )}
    {(result.status != "success" && result.status != "pending") && (
        <h1 className = {styles.invalid}>This link is invalid or has already been used.</h1>
    )}
    </div>
    </main>
    </>
)
}

export default VerifyEmailPage; 