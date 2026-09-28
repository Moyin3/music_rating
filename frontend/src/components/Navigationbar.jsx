import Searchbar from "./SearchBar";
import LoginButton from "./LoginButton";
import { BrowserRouter, Link } from "react-router";
import SignUpButton from "./SignUpButton";
import styles from "./styles/Navigationbar.module.css";

const NavigationBar = () => {
    return(
        <div className={styles.navBar}>
            <Link to= "/">
            <button className= {styles.webpageName}>RipeGrapes</button>
            </Link>
            <Searchbar  className="searchbar"/>
           {/* <button>Artists</button> 
            <button>Albums</button>
            <button>Tracks</button> */}
            <SignUpButton className= {styles.signUp} />
            <LoginButton className= {styles.login}/>
        </div>
    )
}

export default NavigationBar;
