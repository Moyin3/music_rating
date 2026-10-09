import Navigationbar from "../components/Navigationbar";
import SignUpButton from "../components/SignUpButton";
import styles from "./styles/HomePage.module.css";

const HomePage = () => {
    return(
        <>
        <Navigationbar />
        <main className = {styles.homeGrid}>
        <div className={styles.homeDiv}>
        <h1 className={styles.homepageDesc}>Where music opinion is transformed into receipts and numbers</h1>
        <h2 className={styles.homepageEnc}>Start rating your favourite music now</h2>
        <SignUpButton className={styles.homepageButton}/>
        </div>
        </main>
        </>
    )
}

export default HomePage;