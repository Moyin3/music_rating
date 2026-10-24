import NavigationBar from "../components/Navigationbar";
import SignUpForm from "../components/SignUpForm";
import styles from "./styles/SignUpPage.module.css";

const SignUpPage = () => {
    return (
        <>
        <NavigationBar />
        <main className = {styles.signUpGrid}>
        <div className = {styles.signUpDiv}>
        <SignUpForm />
        </div>
        </main>
        </>

    )
}
export default SignUpPage;