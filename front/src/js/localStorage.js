class LocalStorageWrapper {
    constructor(name) {
        this.name = name
        this.key = this.getLocalStorageKey(name)
    }

    getLocalStorageKey(name) {
        if (window.pilot.desk.id && window.pilot.user.id)
            return name + "-desk" + window.pilot.desk.id + "-user" + window.pilot.user.id
        else return name
    }

    get() {
        // Accessing window.localStorage sometime produce an "Access is denied" on IE.
        // Handle this case with a try catch
        try {
            if (!window.localStorage) return null
        } catch (e) {
            return null
        }

        // Handle values stored in the old key, which were without the desk/user ids,
        // and migrate it to the new format.
        let oldValue = window.localStorage.getItem(this.name)
        if (oldValue && this.key != this.name) {
            window.localStorage.setItem(this.key, oldValue)
            window.localStorage.removeItem(this.name)
        }

        let value = window.localStorage.getItem(this.key)

        // Handle values not stored as stringified JSON
        try {
            return JSON.parse(value)
        } catch (e) {
            return value
        }
    }

    set(value) {
        // Accessing window.localStorage sometime produce an "Access is denied" on IE 10/11.
        // Handle this case with a try catch
        try {
            if (!window.localStorage) return
        } catch (e) {
            return
        }

        value = JSON.stringify(value)

        return window.localStorage.setItem(this.key, value)
    }
}

export { LocalStorageWrapper }
