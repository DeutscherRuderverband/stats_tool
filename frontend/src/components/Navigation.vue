<script>
import {useGlobalState} from "@/stores/globalStore";
export default {
  name: "navigation",
  data() {
    return {
      scrolledNav: null,
      mobile: null,
      mobileNav: null,
      currentSubMenu: {},
      showSubMenu: false,
      windowWidth: null,
      navigationLinks: [
        {
          displayName: "Kalender",
          link: "/"
        },
        {
          displayName: "Berichte",
          link: "/berichte",
        },
        {
          displayName: "Rennstrukturanalyse",
          link: "/rennstrukturanalyse",
        },
        {
          displayName: "Athleten",
          link: "/athleten",
        },
        {
          displayName: "Teams",
          link: "/teams",
        },
        {
          displayName: "Medaillenspiegel",
          link: "/medaillenspiegel",
        }
      ]
    };
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
  },
  mounted() {
    window.addEventListener('scroll', this.updateScroll);
  },

  methods: {
     isActive(link, linkName) {
       if (linkName !== "Kalender") {
         return this.$route.path.startsWith(link);
       } else {
         return false;
       }
    },
    closeMobileNav() {
      this.mobileNav = false;
    },
    include () {
        return [document.querySelector('.included')]
      },
    toggleMobileNav() {
      this.mobileNav = !this.mobileNav;
    },
    onMouseOverSubMenu() {
      this.showSubMenu = true;
    },
    onMouseLeaveNav() {
      this.showSubMenu = false;
    },
    updateScroll() {
      const scrollPosition = window.scrollY;
      const globalStore = useGlobalState();
      if(!this.mobile && scrollPosition > 50) {
        this.scrolledNav = true;
        globalStore.setHeaderReducedState(true);
        return;
      }
      if(!this.mobile && scrollPosition <= 50) {
        globalStore.setHeaderReducedState(false);
      }
      this.scrolledNav = false;
    },
    checkScreen() {
      this.windowWidth = window.innerWidth;
      if (this.windowWidth < 890) {
        this.mobile = true;
        document.querySelector('body').style.paddingTop = '4.5em';
        return;
      }
      this.mobile = false;
      this.mobileNav = false;
      document.querySelector('body').style.paddingTop = '10.6em';
      return;
    }
  }
}
</script>

<template>
  <header v-bind:style='{"padding-top" : (mobile ? "0em" : "18px" )}' :class="{ 'scrolled-nav': scrolledNav }">
    <!-- Title element -->
    <v-container class="title-container px-10 py-0" v-show="!mobile">
      <p>DRV Stats</p>
      <p><a href="https://www.rudern.de/">Deutscher Ruderverband e.V.</a></p>
    </v-container>

    <!-- navbar incl. mobile navbar -->
    <v-container :class="mobile ? 'px-5 py-0' : 'px-10 py-0'">
      <nav v-bind:style='{"padding-top" : (!mobile ? "2.5em" : "15px"), "padding-bottom" : (!mobile ? "10px" : "0")}'
          @mouseleave="onMouseLeaveNav">
        <div class="nav-links-wrapper">
          <div v-show="!mobile" class="branding">
            <RouterLink to="/"><img alt="DRV Logo" class="logo" style="margin-top: 5px;" src="@/assets/images/DRV_Logo_white.svg" width="105" height="45"/></RouterLink>
          </div>
          <div v-show="mobile" class="branding-mobile">
            <RouterLink to="/"><img alt="DRV Logo" class="logo" src="@/assets/images/DRV_Logo_white.svg" width="80" height="40"/></RouterLink>
          </div>
          <ul v-show="!mobile" class="navigation" :class="{'collapsed-nav': !showSubMenu, 'expanded': showSubMenu}">
            <li v-for="navEntry in navigationLinks">
              <!-- To activate the submenu add this (@mouseover="expandSubPageMenu(navEntry)") to the Link below -->
              <RouterLink :class="isActive(navEntry.link, navEntry.displayName) ?
                'router-link-exact-active' : null"
                :to="navEntry.link"><b>{{ navEntry.displayName }}</b></RouterLink>
            </li>
          </ul>
        </div>
        <div id="sub-menu" v-show="showSubMenu" @mouseover="onMouseOverSubMenu">
          <ul>
            <li v-for="subMenuLink in currentSubMenu">
              <RouterLink :to="subMenuLink.linkTo">{{ subMenuLink.subPageName }}</RouterLink>
            </li>
          </ul>
        </div>
        <p v-show="mobile" id="mobile-title">DRV Stats</p>
        <div v-show="mobile" class="icon included">
          <i @click="toggleMobileNav" class="far fa-bars" :class="{ 'icon-active': mobileNav }"></i>
        </div>
        <transition name="mobile-nav">
          <div v-show="mobileNav" class="dropdown-nav" v-click-outside="{handler: closeMobileNav, include}">
            <h2 id="nav-header"><a href="https://www.rudern.de/">Deutscher Ruderverband e.V.</a></h2>
            <ul>
              <li v-for="navEntry in navigationLinks">
                <RouterLink :to="navEntry.link" @click="toggleMobileNav"><b>{{ navEntry.displayName }}</b></RouterLink>
              </li>
            </ul>
          </div>
        </transition>
      </nav>
    </v-container>
  </header>
</template>

<style lang="scss" scoped>
header {
  top: 0;
  left: 0;
  right: 0;
  position: fixed;
  background-color: #5cc5ed;
  width: 100%;
  padding-bottom: 0.95em;
  z-index: 99;

  a.router-link-exact-active {
    color: #1369b0;
  }

  nav {
    display: flex;
    flex-direction: column;
    padding: 12px 0;
    margin: 0 auto;
    @media (max-width: 890px) {
      flex-direction: row;
    }

    ul {
      list-style: none;
    }

    li {
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 0 0.625rem;
    }

    a {
      color: #fff;
      font-weight: 500;
    }

    a:hover {
      color: #1369b0;
    }

    .navigation {
      display: flex;
      align-items: center;
      flex: 1;
      padding: 0 16px;
    }

    .icon {
      display: flex;
      align-items: center;
      position: absolute;
      top: 0;
      right: 10px;
      height: 100%;

      i {
        cursor: pointer;
        font-size: 24px;
        color: #fff;
        transition: 0.8s ease all;
      }
    }

    #mobile-title {
      font-size: medium;
      margin-left: auto;
      margin-right: auto;
      margin-top: 0.3em;
      width: 9.5em;
      color: #fff;
    }

    .icon-active {
      transform: rotate(180deg);

    }

    .dropdown-nav {
      z-index: 1;
      display: flex;
      flex-direction: column;
      position: fixed;
      width: 100%;
      max-width: 250px;
      height: 100%;
      background-color: #646464;;
      top: 0;
      left: 0;

      ul {
        padding-top: 1em;
      }

      li {
        margin-left: 0;
        padding: 0.6rem 1rem;

        a {
          color: #d8d8d8;
        }
      }

      #nav-header {
        font-size: 12px;
        padding-left: 1rem;
        padding-top: 28.5px;
        padding-bottom: 28.5px;
        background-color: #505050;
      }

      a:hover {
        color: white;
      }
      a.router-link-exact-active {
        color: white;
      }
    }

    .mobile-nav-enter-active,
    .mobile-nav-leave-active {
      transition: 0.5s ease all;
    }

    .mobile-nav-enter-from,
    .mobile-nav-leave-to {
      transform: translateX(-250px);
    }

    .mobile-nav-enter-to {
      transform: translateX(0);
    }
  }
}

header::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    @media(min-width: 890px) {
      border-top: 0.5rem solid #008000;
      border-bottom: 1rem solid #1369b0;
    }
    border-top: 0.25rem solid #008000;
    border-bottom: 0.5rem solid #1369b0;
}

.scrolled-nav {
  padding-top: 0px !important;
  nav {
    padding-top: 0px !important;
  }
  .title-container {
    display: none;
  }
}

p {
  font-size: 14px;
  text-transform: uppercase;
  position: relative;
  display: flex;
  flex-direction: row;
  transition: 0.5s ease all;
  color: #ffffff;

  a {
    color: #ffffff;
  }

  a:hover {
    color: #1369b0;
  }

  li {
    list-style: none;
    margin-left: auto;
  }
}

.title-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0 auto;
}

#sub-menu {
  display: block;
  clear: both;
  margin-top: 20px;
  padding: 15px 0;
}

#sub-menu a {
  color: white;
}

#sub-menu li {
  font-style: normal;
  text-transform: none;
  padding: 5px 0;
}

#sub-menu li a:hover {
  color: #1369b0;
}

.nav-links-wrapper {
  display: flex;
}

</style>
