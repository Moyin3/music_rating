import { useParams } from "react-router";
import post from "../functions/post";

const VerifyEmailPage = async (event) =>{
let params = useParams();
const data = {"key":params.key}

const response = await post({"url": "api/auth/registration/verify-email/", "data": data});
}

export default VerifyEmailPage; 