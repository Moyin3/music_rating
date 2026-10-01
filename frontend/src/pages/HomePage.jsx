import Navigationbar from "../components/Navigationbar";
import SignUpButton from "../components/SignUpButton";
import styles from "./styles/HomePage.module.css";

const HomePage = () => {
    return(
        <>
        <Navigationbar />
        <body>
        <div className={styles.homeDiv}>
        <h1 className={styles.homepageDesc}>A place for music opinion to be transformed into receipts and numbers</h1>
        <h2 className={styles.homepageEnc}>Start rating your favourite music now</h2>
        <SignUpButton />
        </div>
        </body>
        </>
    )
}

export default HomePage;