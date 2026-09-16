import NavigationBar from "../components/Navigationbar";
import ResetPasswordForm from "../components/ResetPasswordForm";
import {useParams} from "react-router";

const ResetPasswordPage = () => {
let params = useParams();
const uid = params.uid;
const token = params.token;
return(
    <>
    <NavigationBar />
    <ResetPasswordForm uid = {uid} token = {token} />
    </>
)
}

export default ResetPasswordPage;