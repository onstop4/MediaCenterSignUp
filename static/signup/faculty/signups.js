const { createApp } = Vue

// Taken from https://stackoverflow.com/a/15724300.
function getCookie(name) {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop().split(';').shift()
}

// Taken from https://stackoverflow.com/a/29774197.
function getDateFormatted(date) {
    const offset = date.getTimezoneOffset()
    date = new Date(date.getTime() - (offset * 60 * 1000))
    return date.toISOString().split('T')[0]
}

axiosSettings = { headers: { "X-CSRFToken": getCookie('csrftoken') } }

scriptData = JSON.parse(document.getElementById('script_data').textContent)

// filterModal = new bootstrap.Modal(document.getElementById('filterModal'), { 'keyboard': false })

createApp({
    components: {
        'table-header': {
            props: ['text', 'sortKey', 'currentSortKey'],
            template: `<th scope="col" :class="[isCurrentSortKey ? 'fw-bold' : 'fw-normal']" @click.stop="changeSort">{{ text }}</th>`,
            methods: {
                changeSort() {
                    this.$emit('changeSort', this.sortKey)
                }
            },
            computed: {
                isCurrentSortKey() {
                    return this.sortKey === this.currentSortKey
                }
            }
        }
    },
    data() {
        return { signups: [], errorOccurred: false, sortKey: scriptData.default_sort, sortDescending: false, periodNumberInputChecked: false, showFilterModal: false, filterInputs: {}, filters: { date: new Date(scriptData.default_date), periodNumber: null, studentName: null, studentId: null, reason: "" } }
    },
    methods: {
        getURLQueryParameters() {
            let params = `class_period__date=${getDateFormatted(this.filters.date)}`

            // Won't filter by period number if this.filters.periodNumber is not a valid number.
            if (this.periodNumberInputChecked && this.filters.periodNumber !== null) {
                params += `&class_period__number=${this.filters.periodNumber}`
            }

            if (this.filters.studentName) {
                params += `&search=${this.filters.studentName}`
            }

            if (this.filters.studentId) {
                params += `&student__info__id=${this.filters.studentId}`
            }

            if (this.filters.reason) {
                params += `&reason=${this.filters.reason}`
            }

            params += `&ordering=` + (this.sortDescending ? `-${this.sortKey}` : this.sortKey)

            return params
        },
        updateSignups() {
            let url = `${scriptData.list_url}?${this.getURLQueryParameters()}`

            axios.get(url).then(response => { this.signups = response.data }).catch(() => { this.errorOccurred = true })
        },
        downloadSpreadsheet() {
            let url = `${scriptData.spreadsheet_url}?${this.getURLQueryParameters()}`

            window.open(url, '_blank').focus()
        },
        confirmAttendance(signUpId, will_confirm) {
            axios.patch(`${scriptData.individual_url}${signUpId}/`, { 'attendance_confirmed': will_confirm }, axiosSettings).then(response => {
                this.signups.filter(signup => signup.id == signUpId)[0].attendance_confirmed = response.data.attendance_confirmed
            }).catch(() => { this.errorOccurred = true })
        },
        sort(key) {
            if (this.sortKey === key && !this.sortDescending) {
                this.sortDescending = true
            } else {
                this.sortKey = key
                this.sortDescending = false
            }
            this.updateSignups()
        },
        cancelFilterEditing() {
            this.showFilterModal = false
            this.filterInputs = { ...this.filters }
        },
        saveFilters() {
            this.showFilterModal = false

            // Won't save anything related to period number if this.filterInputs.periodNumber is not a valid number.
            if (this.periodNumberInputChecked && this.filterInputs.periodNumber === null) {
                this.periodNumberInputChecked = false
            }

            this.filters = { ...this.filterInputs }
            this.updateSignups()
        },
        signupCheckboxToggled() {
            let selectedSignups = this.signups.filter(signup => signup.selected)
            let selectAllCheckbox = document.querySelector("#select-all-signups-checkbox")

            if (selectedSignups.length === this.signups.length) {
                selectAllCheckbox.checked = true
                selectAllCheckbox.indeterminate = false
            } else if (selectedSignups.length > 0) {
                selectAllCheckbox.checked = false
                selectAllCheckbox.indeterminate = true
            } else {
                selectAllCheckbox.checked = false
                selectAllCheckbox.indeterminate = false
            }
        }, selectAllOrNone() {
            let selectedSignups = this.signups.filter(signup => signup.selected)

            let selectAllCheckbox = document.querySelector("#select-all-signups-checkbox")
            selectAllCheckbox.indeterminate = false

            let toChange = !(selectedSignups.length === this.signups.length)
            selectAllCheckbox.checked = toChange
            this.signups.forEach(signup => { signup.selected = toChange })

            if (selectedSignups.length === this.signups.length) {
                selectAllCheckbox.checked = false
                selectedSignups.forEach(signup => { signup.selected = false })
            } else {
                selectAllCheckbox.checked = true
                selectAllCheckbox.indeterminate = false
            }
        },
        removeMultiple() {
            let ids = this.signups.filter(signup => signup.selected).map(signup => `id=${signup.id}`).join("&");

            axios.post(scriptData.delete_multiple_signups, ids, axiosSettings).then(() => {
                this.signups = this.signups.filter(signup => !signup.selected)

                let selectAllCheckbox = document.querySelector("#select-all-signups-checkbox")
                selectAllCheckbox.checked = false
                selectAllCheckbox.indeterminate = false
            }).catch(() => { this.errorOccurred = true })
        }
    },
    computed: {
        stringDateFilter: {
            get() {
                return getDateFormatted(this.filterInputs.date)
            },
            set(dateString) {
                let [year, month, day] = dateString.split('-')
                this.filterInputs.date = new Date(year, month - 1, day)
            }
        },
        readableDateFilter() {
            return new Intl.DateTimeFormat('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }).format(this.filters.date)
        },
        readableReasonFilter() {
            switch (this.filters.reason) {
                case 'L':
                    return 'lunch'
                case 'S:':
                    return 'study hall'
                default:
                    return ''
            }
        },
        moreThanDateFilterActive() {
            return (this.filters.periodNumber || this.filters.studentName || this.filters.studentId || this.filters.reason)
        },
        noSignupSelected() {
            return !this.signups.some(signup => signup.selected)
        }
    },
    mounted() {
        this.updateSignups()
        this.filterInputs = { ...this.filters }
    }
}).mount('#app')
