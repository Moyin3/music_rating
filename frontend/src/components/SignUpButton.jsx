 import { Link } from 'react-router';
 import styles from "./styles/SignUpButton.module.css";

 const SignUpButton = ({className}) => {
 return(
    <>
    <Link to= "/sign-up" className = {className}>
   Sign up
 </Link>
 </>
 )
 };

export default SignUpButton;