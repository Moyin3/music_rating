import LoginForm from '../components/LoginForm';
import NavigationBar from '../components/Navigationbar';
import styles from './styles/LoginPage.module.css';

const LoginPage = () => {
    return(
    <>
    <NavigationBar />
    <main className= {styles.loginGrid}>
    <div className= {styles.loginDiv}>
    <LoginForm />
    </div>
    </main>
    </>
    )
}

       

export default LoginPage;