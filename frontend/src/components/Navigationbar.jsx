import Searchbar from "./SearchBar";
import LoginButton from "./LoginButton";
import { BrowserRouter, Link } from "react-router";
import SignUpButton from "./SignUpButton";
import styles from "./styles/Navigationbar.module.css";

const NavigationBar = () => {
    return(
        <div className={styles.navBar}>
            <Link to= "/" className= {styles.webpageName}>
            RipeGrapes
            </Link>
            <Searchbar  className="searchbar"/>
           {/* <button>Artists</button> 
            <button>Albums</button>
            <button>Tracks</button> */}
            <div className = {styles.signUpAndLogin}>
            <SignUpButton className = {styles.signUpButton}/>
            <LoginButton />
            </div>
        </div>
    )
}

export default NavigationBar;
