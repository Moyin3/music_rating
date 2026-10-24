import { useEffect, useRef, useContext, useState } from "react";
import { handleGoogleCallback } from "../functions/GoogleAuth";
import NavigationBar from "../components/Navigationbar";
import { useNavigate } from "react-router";
import LoginCheck from "../functions/LoginCheck";
import AuthContext from '../functions/AuthContext';

const GoogleCallbackPage = () =>{
const navigate = useNavigate();
const calledRef = useRef(false);
const { user, setUser } = useContext(AuthContext);
const [failure, setFailure] = useState(false);
const [errors, setErrors] = useState([]);
const GENERAL = "non_field_errors";

function normaliseErrors(body) {
  if (typeof body === "string") return { [GENERAL]: [body] };
  if (!body || typeof body !== "object") return { [GENERAL]: ["Something went wrong"] };

  const out = {};
  for (const [key, val] of Object.entries(body)) {
    out[key === "detail" ? GENERAL : key] = [].concat(val).map(String);
  }
  return out;
}
useEffect(()=>{
    if (calledRef.current) return;
    calledRef.current = true;
    handleGoogleCallback().then(async (result) => {
        console.log("Let's see what gmail login is returning", result);
        if (result.success) {
            setUser(await LoginCheck());
            navigate('/')
        } else{
            setFailure(true);
            const flat = Object.entries(normaliseErrors(result.error)).flatMap(([field, msgs]) =>
                 msgs.map(m => (field === GENERAL ? m : `${field}: ${m}`))
            );
            console.log("messages:", flat);
            setErrors(flat);
        }
    })
}, []);
console.log("What's going on here", errors);
return(
    <>
    <NavigationBar />
    {!failure && (
    <div className = "pending">Logging in...</div>
    )}
    {failure && (
        <div className = "alert">{errors}</div>
    )}
    </>
)
}

export default GoogleCallbackPage;