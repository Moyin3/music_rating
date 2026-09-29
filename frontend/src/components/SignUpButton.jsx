 import { Link } from 'react-router';
 import styles from "./styles/SignUpButton.module.css";

 const SignUpButton = ({className}) => {
 return(
    <>
    <Link to= "/sign-up" className = {className}>
 <button className = {styles.signUpBtn}>Sign up</button>
 </Link>
 </>
 )
 };

export default SignUpButton;