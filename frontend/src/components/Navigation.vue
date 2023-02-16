<script>
export default {
  name: "navigation",
  data() {
    return {
      scrollPosition: null,
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
    checkScreen() {
      this.windowWidth = window.innerWidth;
      if (this.windowWidth <= 750) {
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
  <header>
  <div class="header-box">
    <header v-bind:style='{"padding-top" : (mobile? "0em" : "18px" )}' :class="{ 'scrolled-nav': scrollPosition }">

      <!-- Title element -->
      <div id="desktop-title" class="title-container" v-show="!mobile">
        <p>U ->- Row</p>
        <p><a href="https://www.rudern.de/">Deutscher Ruderverband e.V.</a></p>
      </div>

      <!-- navbar incl. mobile navbar -->
      <nav v-bind:style='{"padding-top" : (!mobile? "2.5em" : "15px"), "padding-bottom" : (!mobile? "15px" : "5px")}'
           @mouseleave="onMouseLeaveNav">
        <div class="nav-links-wrapper">
          <div v-show="!mobile" class="branding">
            <RouterLink to="/"><img alt="DRV Logo" class="logo" src="@/assets/images/DRV_Logo_white.svg" width="105" height="45"/></RouterLink>
          </div>
          <div v-show="mobile" class="branding-mobile">
            <RouterLink to="/"><img alt="DRV Logo" class="logo" src="@/assets/images/DRV_Logo_white.svg" width="64" height="30"/></RouterLink>
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
        <p v-show="mobile" id="mobile-title">U ->- Row</p>
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
    </header>
  </div>
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
    transition: 0.5s ease all;
    width: 90%;
    margin: 0 auto;
    max-width: 1140px;
    @media (max-width: 750px) {
      flex-direction: row;
    }

    ul {
      list-style: none;
    }

    li {
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-style: italic;
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
      margin-left: auto;
      margin-right: auto;
      width: 9em;
      align-self: center;
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
      background-color: #000000;
      top: 0;
      left: 0;

      li {
        margin-left: 0;
        color: #fff;
        padding: 0.6rem 1rem;
      }

      #nav-header {
        font-size: 12px;
        padding: 1.5em;
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

  header::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    @media(min-width: 750px) {
      border-top: 0.5rem solid #008000;
      border-bottom: 1rem solid #1369b0;
    }
    border-top: 0.25rem solid #008000;
    border-bottom: 0.5rem solid #1369b0;
  }
}

p {
  font-size: 14px;
  text-transform: uppercase;
  position: relative;
  display: flex;
  flex-direction: row;
  transition: 0.5s ease all;
  @media(min-width: 1140px) {
    max-width: 1140px;
  }
  color: #d6f0fa;
  font-style: italic;

  a {
    color: #d6f0fa;
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
  width: 90%;
  margin: 0 auto;
  max-width: 1140px;
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
